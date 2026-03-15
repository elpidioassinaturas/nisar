#!/usr/bin/env python3
"""
NISAR Downloader — Interface Web
Versão: 0.0.3
"""
import json
import os
import queue
import threading
from datetime import datetime
from pathlib import Path

import yaml
from flask import Flask, Response, jsonify, render_template, request

try:
    import asf_search as asf
except ImportError:
    asf = None

try:
    from extract_nisar import extract_layers, AVAILABLE_LAYERS
except ImportError:
    extract_layers = None
    AVAILABLE_LAYERS = []

app = Flask(__name__)

CONFIG_PATH = Path("nisar_config.yaml")
LOG_QUEUE: queue.Queue = queue.Queue()
DOWNLOAD_STATUS = {"running": False, "done": 0, "total": 0, "error": None}

EXTRACT_LOG_QUEUE: queue.Queue = queue.Queue()
EXTRACT_STATUS = {"running": False, "files": [], "error": None}


# ── Config helpers ────────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(data: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    cfg = load_config()
    return jsonify({
        "username":     cfg.get("earthdata", {}).get("username", ""),
        "password":     cfg.get("earthdata", {}).get("password", ""),
        "product_type": cfg.get("search", {}).get("product_type", "GCOV"),
        "start_date":   cfg.get("search", {}).get("start_date", "2025-10-17"),
        "end_date":     cfg.get("search", {}).get("end_date", "2026-01-20"),
        "max_results":  cfg.get("search", {}).get("max_results", 50),
        "aoi_wkt":      cfg.get("search", {}).get("aoi_wkt", "POLYGON((-73.9 -33.7, -34.8 -33.7, -34.8 5.3, -73.9 5.3, -73.9 -33.7))"),
        "directory":    cfg.get("download", {}).get("directory", "downloads/nisar"),
        "processes":    cfg.get("download", {}).get("processes", 2),
    })


@app.route("/api/config", methods=["POST"])
def post_config():
    d = request.json
    cfg = {
        "earthdata": {"username": d["username"], "password": d["password"]},
        "search": {
            "aoi_wkt":      d["aoi_wkt"],
            "product_type": d["product_type"],
            "start_date":   d["start_date"],
            "end_date":     d["end_date"],
            "max_results":  int(d["max_results"]),
        },
        "download": {
            "directory": d["directory"],
            "processes": int(d["processes"]),
        },
    }
    save_config(cfg)
    return jsonify({"ok": True})


@app.route("/api/search", methods=["POST"])
def api_search():
    if not asf:
        return jsonify({"error": "asf_search não instalado. Execute: pip install asf_search"}), 500
    cfg = load_config()
    s = cfg.get("search", {})
    try:
        kwargs = dict(
            platform=[asf.PLATFORM.NISAR],
            processingLevel=s.get("product_type", "GCOV"),
            start=s.get("start_date"),
            end=s.get("end_date"),
            maxResults=s.get("max_results", 50),
        )
        aoi = s.get("aoi_wkt", "").strip()
        if aoi:
            kwargs["intersectsWith"] = aoi
        results = asf.search(**kwargs)
        items = []
        for r in results:
            p = r.properties

            # bytes é um dict: {filename: {bytes: N, ...}} — soma todos os arquivos
            raw_bytes = p.get("bytes", None)
            if isinstance(raw_bytes, dict):
                total_bytes = sum(
                    v.get("bytes", 0) if isinstance(v, dict) else (v or 0)
                    for v in raw_bytes.values()
                )
            elif isinstance(raw_bytes, (int, float)):
                total_bytes = raw_bytes
            else:
                total_bytes = 0
            try:
                size_mb = round(float(total_bytes) / 1e6, 1)
            except (TypeError, ValueError):
                size_mb = 0

            # browse: lista de URLs de thumbnails PNG
            browse_urls = p.get("browse") or []
            thumb = browse_urls[0] if browse_urls else None

            # Bounding box em graus (WGS84) extraído da geometria GeoJSON
            bbox = None
            utm_zone = None
            try:
                coords = r.geometry["coordinates"][0]
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                min_lon, max_lon = min(lons), max(lons)
                min_lat, max_lat = min(lats), max(lats)
                bbox = {
                    "minLon": round(min_lon, 2),
                    "maxLon": round(max_lon, 2),
                    "minLat": round(min_lat, 2),
                    "maxLat": round(max_lat, 2),
                }
                # Zona UTM derivada do centro do polígono
                center_lon = (min_lon + max_lon) / 2
                center_lat = (min_lat + max_lat) / 2
                zone_num = int((center_lon + 180) / 6) + 1
                hemi = "N" if center_lat >= 0 else "S"
                epsg = 32600 + zone_num if hemi == "N" else 32700 + zone_num
                utm_zone = {"zone": f"{zone_num}{hemi}", "epsg": epsg}
            except Exception:
                pass

            items.append({
                "name":      str(p.get("sceneName") or ""),
                "product":   str(p.get("processingLevel") or ""),
                "date":      str(p.get("startTime") or ""),
                "size_mb":   size_mb,
                "url":       str(p.get("url") or ""),
                "thumb":     thumb,
                "direction": str(p.get("flightDirection") or ""),
                "orbit":     p.get("orbit"),
                "utm_zone":  utm_zone,
                "bbox":      bbox,
            })
        return jsonify({"results": items, "total": len(items)})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500


def _download_worker(results_json: list, cfg: dict):
    global DOWNLOAD_STATUS
    DOWNLOAD_STATUS.update({"running": True, "done": 0, "total": len(results_json), "error": None})
    try:
        earthdata = cfg.get("earthdata", {})
        session = asf.ASFSession().auth_with_creds(earthdata["username"], earthdata["password"])
        out_dir = cfg.get("download", {}).get("directory", "downloads/nisar")
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        # Re-search to get ASFProduct objects
        names = [r["name"] for r in results_json]
        products = asf.granule_search(names)

        LOG_QUEUE.put(f"Iniciando download de {len(products)} produto(s)...")
        for i, product in enumerate(products, 1):
            name = product.properties.get("sceneName", f"produto_{i}")
            LOG_QUEUE.put(f"[{i}/{len(products)}] Baixando: {name}")
            try:
                product.download(path=out_dir, session=session)
                DOWNLOAD_STATUS["done"] = i
                LOG_QUEUE.put(f"  ✓ Concluído: {name}")
            except Exception as e:
                LOG_QUEUE.put(f"  ✗ Erro: {e}")
        LOG_QUEUE.put("__DONE__")
    except Exception as e:
        DOWNLOAD_STATUS["error"] = str(e)
        LOG_QUEUE.put(f"Erro de autenticação: {e}")
        LOG_QUEUE.put("__DONE__")
    finally:
        DOWNLOAD_STATUS["running"] = False


@app.route("/api/download", methods=["POST"])
def api_download():
    if DOWNLOAD_STATUS["running"]:
        return jsonify({"error": "Download já em andamento"}), 400
    data = request.json or {}
    results = data.get("results", [])
    if not results:
        return jsonify({"error": "Nenhum produto selecionado"}), 400
    cfg = load_config()
    t = threading.Thread(target=_download_worker, args=(results, cfg), daemon=True)
    t.start()
    return jsonify({"ok": True, "total": len(results)})


@app.route("/api/stream")
def api_stream():
    def gen():
        while True:
            try:
                msg = LOG_QUEUE.get(timeout=30)
                yield f"data: {json.dumps({'msg': msg})}\n\n"
                if msg == "__DONE__":
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'msg': '__PING__'})}\n\n"
    return Response(gen(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/status")
def api_status():
    return jsonify(DOWNLOAD_STATUS)


@app.route("/api/files")
def api_files():
    cfg = load_config()
    out_dir = Path(cfg.get("download", {}).get("directory", "downloads/nisar"))
    files = []
    if out_dir.exists():
        for f in sorted(out_dir.iterdir()):
            if f.is_file():
                files.append({
                    "name": f.name,
                    "size_mb": round(f.stat().st_size / 1e6, 1),
                    "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                })
    return jsonify({"files": files})


# ── Extract ───────────────────────────────────────────────────────────────────

@app.route("/api/extract-info")
def api_extract_info():
    """Retorna layers disponíveis para extração."""
    return jsonify({"layers": AVAILABLE_LAYERS, "available": extract_layers is not None})


def _extract_worker(h5_path: str, out_dir: str, frequencies: list, layers: list):
    global EXTRACT_STATUS
    EXTRACT_STATUS.update({"running": True, "files": [], "error": None})
    try:
        def log(msg):
            EXTRACT_LOG_QUEUE.put(msg)

        files = extract_layers(h5_path, out_dir, frequencies, layers, log_fn=log)
        EXTRACT_STATUS["files"] = files
    except Exception as e:
        import traceback
        EXTRACT_STATUS["error"] = str(e)
        EXTRACT_LOG_QUEUE.put(f"✗ Erro: {e}")
        EXTRACT_LOG_QUEUE.put(traceback.format_exc())
    finally:
        EXTRACT_STATUS["running"] = False
        EXTRACT_LOG_QUEUE.put("__DONE__")


@app.route("/api/extract", methods=["POST"])
def api_extract():
    if not extract_layers:
        return jsonify({"error": "rasterio não instalado. Execute: pip install rasterio>=1.3"}), 500
    if EXTRACT_STATUS["running"]:
        return jsonify({"error": "Extração já em andamento"}), 400

    data = request.json or {}
    cfg  = load_config()
    h5_file     = data.get("file", "")
    dl_dir      = cfg.get("download", {}).get("directory", "downloads/nisar")
    h5_path     = str(Path(dl_dir) / h5_file)
    out_subdir  = data.get("out_subdir", "geotiff")
    out_dir     = str(Path(dl_dir).parent / out_subdir)
    frequencies = data.get("frequencies", ["frequencyA"])
    layers      = data.get("layers", ["HHHH", "HVHV", "mask"])

    if not Path(h5_path).exists():
        return jsonify({"error": f"Arquivo não encontrado: {h5_path}"}), 404

    # Limpa fila anterior
    while not EXTRACT_LOG_QUEUE.empty():
        try: EXTRACT_LOG_QUEUE.get_nowait()
        except: break

    t = threading.Thread(target=_extract_worker,
                         args=(h5_path, out_dir, frequencies, layers), daemon=True)
    t.start()
    return jsonify({"ok": True, "out_dir": out_dir})


@app.route("/api/extract-stream")
def api_extract_stream():
    def gen():
        while True:
            try:
                msg = EXTRACT_LOG_QUEUE.get(timeout=30)
                yield f"data: {json.dumps({'msg': msg})}\n\n"
                if msg == "__DONE__":
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'msg': '__PING__'})}\n\n"
    return Response(gen(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/extract-status")
def api_extract_status():
    return jsonify(EXTRACT_STATUS)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import webbrowser
    print("=" * 50)
    print("  NISAR Downloader — Interface Web v0.0.3")
    print("  Abrindo em: http://localhost:5000")
    print("  Para encerrar: feche esta janela ou Ctrl+C")
    print("=" * 50)
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False, host="127.0.0.1", port=5000)
