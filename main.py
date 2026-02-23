"""
╔══════════════════════════════════════════════════════════╗
║                     🌐 LinguaFlow                        ║
║     Real-Time Multilingual Translation with EQ           ║
║                                                          ║
║  Bridging languages while preserving emotion & culture   ║
╚══════════════════════════════════════════════════════════╝

Entry point for the LinguaFlow desktop application.
"""

import sys
import os
import logging

# ── Ensure project root is on the path ──
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ── Configure logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-24s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(PROJECT_ROOT, "linguaflow.log"),
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger("LinguaFlow")


def main():
    """Launch the LinguaFlow desktop application."""
    logger.info("=" * 60)
    logger.info("  🌐  LinguaFlow Starting...")
    logger.info("=" * 60)
    logger.info(f"  Python  : {sys.version}")
    logger.info(f"  Platform: {sys.platform}")
    logger.info(f"  CWD     : {PROJECT_ROOT}")

    try:
        import torch
        device = "CUDA" if torch.cuda.is_available() else "CPU"
        logger.info(f"  PyTorch : {torch.__version__} ({device})")
    except ImportError:
        logger.warning("  PyTorch : Not installed!")

    logger.info("=" * 60)

    # ── Launch App ──
    try:
        from ui.app import LinguaFlowApp

        app = LinguaFlowApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)

        logger.info("Application window created, entering main loop...")
        app.mainloop()

    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Run: pip install -r requirements.txt")
        print(f"\n❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt\n")
        sys.exit(1)

    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
