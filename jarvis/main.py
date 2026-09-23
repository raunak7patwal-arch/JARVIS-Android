from jarvis.core.router import Router
from jarvis.skills.system import system_status
from jarvis.skills.information import help_text


BANNER = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

              JARVIS AI CORE v1.0
"""


def main():
    router = Router()

    print(BANNER)
    print("JARVIS: System online.")
    print("Type 'help' for commands.")
    print("Type 'exit' to shutdown.\n")

    while True:
        try:
            user = input("You: ").strip()

            if not user:
                continue

            if user.lower() in ["exit", "quit", "shutdown"]:
                print("JARVIS: Shutting down safely.")
                break

            if user.lower() == "help":
                print(help_text())
                continue

            if user.lower() == "system":
                print(system_status())
                continue

            response = router.handle(user)
            print("JARVIS:", response)
            print()

        except KeyboardInterrupt:
            print("\nJARVIS: Shutdown requested.")
            break

        except Exception as error:
            print("JARVIS: Internal error:", error)


if __name__ == "__main__":
    main()
