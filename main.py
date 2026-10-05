import tkinter as tk
from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView
def abrir(usuario):
    root=tk.Tk(); MainView(root,RestauranteServicio(),usuario); root.mainloop()
def main():
    root=tk.Tk(); LoginView(root,RestauranteServicio(),abrir); root.mainloop()
if __name__=="__main__": main()
