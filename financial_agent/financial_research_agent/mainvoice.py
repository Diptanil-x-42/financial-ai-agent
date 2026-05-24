from .voice_ui import RealtimeApp


def run_ui():
    app = RealtimeApp()
    app.run()  # Runs Textual UI after research completes


if __name__ == "__main__":
    run_ui()