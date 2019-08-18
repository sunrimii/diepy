from core import Diepy


if __name__ == "__main__":
    diepy = Diepy()
    diepy.load_materials()
    
    mode = diepy.select_mode()

    if mode == "single":
        diepy.init_single()
        diepy.add_player()
        
        while diepy.is_running:
            diepy.update_screen()
            event = diepy.get_event()
            diepy.run_logic(event)
    
    # elif mode == "server":
    #     import multiprocessing

    #     from network import Server, Handler


    #     server = Server(("localhost", 5278), Handler)

    # elif mode == "client":
    #     import threading

    #     from network import Client
        

    #     client = Client(addr="127.0.0.1", port=5278)