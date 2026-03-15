#!/usr/bin/env python3
"""
extract_nisar.py
================
Extrai camadas de um arquivo NISAR L2 GCOV (.h5) para GeoTIFF georreferenciados.

Uso:
    from extract_nisar import extract_layers
    files = extract_layers("produto.h5", "out/geotiff", log_fn=print)
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable, List, Optional
import h5py
import numpy as np

try:
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.crs import CRS
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

# Layers disponíveis por frequência
AVAILABLE_LAYERS = ["HHHH", "HVHV", "mask", "numberOfLooks", "rtcGammaToSigmaFactor"]

# dtype de saída por layer
_DTYPES = {
    "HHHH":                 "float32",
    "HVHV":                 "float32",
    "mask":                 "uint8",
    "numberOfLooks":        "float32",
    "rtcGammaToSigmaFactor":"float32",
}

_NODATA = {
    "HHHH":                  float("nan"),
    "HVHV":                  float("nan"),
    "mask":                  255,
    "numberOfLooks":         float("nan"),
    "rtcGammaToSigmaFactor": float("nan"),
}


def extract_layers(
    h5_path: str,
    out_dir: str,
    frequencies: Optional[List[str]] = None,
    layers: Optional[List[str]] = None,
    log_fn: Callable[[str], None] = print,
) -> List[str]:
    """
    Extrai camadas do HDF5 e salva como GeoTIFF.

    Parâmetros
    ----------
    h5_path     : caminho para o .h5 NISAR GCOV
    out_dir     : pasta de saída para os .tif
    frequencies : lista de frequências, ex. ["frequencyA", "frequencyB"]
                  (padrão: apenas frequencyA)
    layers      : lista de layers, ex. ["HHHH", "HVHV"]
                  (padrão: HHHH, HVHV, mask)
    log_fn      : função de logging (default: print)

    Retorna
    -------
    Lista com caminhos dos .tif gerados
    """
    if not HAS_RASTERIO:
        raise RuntimeError("rasterio não instalado. Execute: pip install rasterio>=1.3")

    h5_path = Path(h5_path)
    out_dir  = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if frequencies is None:
        frequencies = ["frequencyA"]
    if layers is None:
        layers = ["HHHH", "HVHV", "mask"]

    # Prefixo do nome gerado a partir do cenário original
    prefix = h5_path.stem  # sem .h5

    generated: List[str] = []

    log_fn(f"Abrindo: {h5_path.name}")
    with h5py.File(h5_path, "r") as f:
        base = "science/LSAR/GCOV/grids"

        for freq in frequencies:
            grp_path = f"{base}/{freq}"
            if grp_path not in f:
                log_fn(f"  ⚠️  Frequência '{freq}' não encontrada no arquivo — pulando")
                continue

            grp = f[grp_path]

            # ── Coordenadas e projeção ──────────────────────────────────
            x_coords = grp["xCoordinates"][:]       # shape (ncols,)
            y_coords = grp["yCoordinates"][:]       # shape (nrows,)
            x_res    = float(grp["xCoordinateSpacing"][()])
            y_res    = float(grp["yCoordinateSpacing"][()])  # negativo

            proj_ds  = grp["projection"]
            epsg     = int(proj_ds.attrs.get("epsg_code", 32718))
            crs      = CRS.from_epsg(epsg)

            # Origem = top-left do pixel superior esquerdo
            # yCoordinates é o centro do pixel; shift de meio pixel
            x_origin = x_coords[0] - x_res / 2
            y_origin = y_coords[0] - y_res / 2   # y_res é negativo → y_origin > y_coords[0]
            transform = from_origin(x_origin, y_origin, abs(x_res), abs(y_res))

            log_fn(f"  📡 {freq}: EPSG:{epsg}  resolução={abs(x_res):.0f}m  "
                   f"dimensão={len(y_coords)}×{len(x_coords)}")

            # ── Layers ─────────────────────────────────────────────────
            for layer in layers:
                if layer not in grp:
                    log_fn(f"    ⚠️  Layer '{layer}' não existe em {freq} — pulando")
                    continue

                log_fn(f"    📊 Lendo {layer}...")
                data   = grp[layer][:]
                dtype  = _DTYPES.get(layer, str(data.dtype))
                nodata = _NODATA.get(layer, None)

                out_name = f"{prefix}_{freq}_{layer}.tif"
                out_path = out_dir / out_name

                log_fn(f"    💾 Salvando {out_name}...")
                with rasterio.open(
                    out_path,
                    "w",
                    driver  = "GTiff",
                    height  = data.shape[0],
                    width   = data.shape[1],
                    count   = 1,
                    dtype   = dtype,
                    crs     = crs,
                    transform = transform,
                    compress  = "lzw",      # compressão leve sem perda
                    nodata   = nodata,
                ) as ds:
                    ds.write(data.astype(dtype), 1)

                size_mb = round(out_path.stat().st_size / 1e6, 1)
                log_fn(f"    ✓ {out_name}  ({size_mb} MB)")
                generated.append(str(out_path))

    log_fn(f"\n✅ Extração concluída: {len(generated)} arquivo(s) em {out_dir}/")
    return generated


# ── CLI rápido ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(description="Extrai layers NISAR HDF5 → GeoTIFF")
    parser.add_argument("h5", help="Arquivo .h5 NISAR GCOV")
    parser.add_argument("--out", default="downloads/geotiff", help="Pasta de saída")
    parser.add_argument("--freq", nargs="+", default=["frequencyA"], help="Frequências")
    parser.add_argument("--layers", nargs="+", default=["HHHH","HVHV","mask"],
                        help="Layers a extrair")
    args = parser.parse_args()
    files = extract_layers(args.h5, args.out, args.freq, args.layers)
    for f in files:
        print(f)
