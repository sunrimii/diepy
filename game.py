from core import Diepy

addr = "127.0.0.1"
port = 5278
if __name__ == "__main__":
    
    diepy = Diepy()
    mode = diepy.select_mode()

    if mode == "single":
        while diepy.is_running:
            events = diepy.get_events()
            diepy.run_logic(events)
            diepy.update_screen()
    
    elif mode == "server":
        import multiprocessing

        from network import Server


        server = Server()

    elif mode == "client":
        import threading

        from network import Client
        
        