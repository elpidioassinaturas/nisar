#!/usr/bin/env python3
"""
NISAR Satellite Data Downloader
================================
Versão: 0.0.1
Repositório: https://github.com/elpidioassinaturas/nisar

Faz busca e download de produtos NISAR via ASF DAAC usando a biblioteca asf_search.

Uso:
    python download_nisar.py --config nisar_config.yaml --dry-run
    python download_nisar.py --config nisar_config.yaml --limit 5
    python download_nisar.py --config nisar_config.yaml
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Verifica se asf_search está instalado
try:
    import asf_search as asf
except ImportError:
    print("ERRO: Pacote 'asf_search' não encontrado.")
    print("Instale com: pip install asf_search")
    sys.exit(1)


# ─── Logging ──────────────────────────────────────────────────────────────────

def setup_logging(log_file: str = "nisar_download.log") -> logging.Logger:
    """Configura logging para console e arquivo."""
    logger = logging.getLogger("nisar_downloader")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    # Arquivo
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


# ─── Config ───────────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    """Carrega o arquivo de configuração YAML."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {config_path}\n"
            "Copie 'nisar_config.yaml.example' para 'nisar_config.yaml' e preencha suas credenciais."
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Auth ─────────────────────────────────────────────────────────────────────

def authenticate(config: dict, logger: logging.Logger) -> asf.ASFSession:
    """Autentica na NASA Earthdata usando credenciais do config."""
    user = config.get("earthdata", {}).get("username", "")
    pwd  = config.get("earthdata", {}).get("password", "")

    if not user or not pwd:
        logger.error("Credenciais Earthdata não configuradas em nisar_config.yaml")
        logger.error("Preencha 'earthdata.username' e 'earthdata.password'")
        sys.exit(1)

    try:
        session = asf.ASFSession().auth_with_creds(user, pwd)
        logger.info(f"Autenticado como: {user}")
        return session
    except Exception as e:
        logger.error(f"Falha na autenticação: {e}")
        sys.exit(1)


# ─── Search ───────────────────────────────────────────────────────────────────

def search_products(config: dict, logger: logging.Logger, limit: int | None = None) -> asf.ASFSearchResults:
    """Busca produtos NISAR com base nos parâmetros do config."""
    search_cfg = config.get("search", {})

    aoi        = search_cfg.get("aoi_wkt")
    start_date = search_cfg.get("start_date")
    end_date   = search_cfg.get("end_date")
    product_type = search_cfg.get("product_type", "GCOV")
    beam_mode  = search_cfg.get("beam_mode")

    logger.info("Iniciando busca de produtos NISAR...")
    logger.info(f"  Plataforma  : NISAR")
    logger.info(f"  Produto     : {product_type}")
    logger.info(f"  Período     : {start_date} → {end_date}")
    logger.info(f"  AOI         : {aoi[:80]}..." if aoi and len(aoi) > 80 else f"  AOI         : {aoi}")

    kwargs = dict(
        platform=[asf.PLATFORM.NISAR],
        processingLevel=product_type,
        start=start_date,
        end=end_date,
    )
    if aoi:
        kwargs["intersectsWith"] = aoi
    if beam_mode:
        kwargs["beamMode"] = beam_mode
    if limit:
        kwargs["maxResults"] = limit

    try:
        results = asf.search(**kwargs)
        logger.info(f"Produtos encontrados: {len(results)}")
        return results
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        sys.exit(1)


# ─── Download ─────────────────────────────────────────────────────────────────

def download_products(
    results: asf.ASFSearchResults,
    session: asf.ASFSession,
    output_dir: str,
    logger: logging.Logger,
    processes: int = 4,
) -> None:
    """Faz o download dos produtos encontrados."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Iniciando download de {len(results)} produto(s) em: {out_path.resolve()}")
    logger.info(f"  Processos paralelos: {processes}")

    try:
        results.download(path=str(out_path), session=session, processes=processes)
        logger.info("Download concluído!")
    except Exception as e:
        logger.error(f"Erro durante o download: {e}")
        raise


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Busca e baixa dados NISAR do ASF DAAC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--config",   default="nisar_config.yaml", help="Caminho para o arquivo de configuração YAML")
    parser.add_argument("--dry-run",  action="store_true",          help="Lista produtos sem fazer download")
    parser.add_argument("--limit",    type=int, default=None,       help="Limita o número de produtos (útil para testes)")
    parser.add_argument("--log",      default="nisar_download.log", help="Arquivo de log")
    args = parser.parse_args()

    logger = setup_logging(args.log)
    logger.info("=" * 60)
    logger.info("NISAR Downloader v0.0.1")
    logger.info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Carrega config
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    out_dir = config.get("output", {}).get("directory", "downloads/nisar")

    # Busca produtos
    limit = args.limit or config.get("search", {}).get("max_results")
    results = search_products(config, logger, limit=limit)

    if len(results) == 0:
        logger.warning("Nenhum produto encontrado com os filtros atuais. Revise o config.")
        sys.exit(0)

    # Dry-run: apenas lista
    if args.dry_run:
        logger.info("=== DRY-RUN: listando produtos (sem download) ===")
        for i, r in enumerate(results, 1):
            logger.info(f"  [{i:03d}] {r.properties.get('sceneName', 'N/A')} | {r.properties.get('processingDate', 'N/A')}")
        logger.info("Dry-run concluído. Use sem --dry-run para baixar.")
        sys.exit(0)

    # Autentica e baixa
    session = authenticate(config, logger)
    processes = config.get("download", {}).get("processes", 4)
    download_products(results, session, out_dir, logger, processes=processes)

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
