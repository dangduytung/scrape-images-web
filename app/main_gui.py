import tkinter as tk
from tkinter import ttk
import main as ScrapeService

# root window
root = tk.Tk()
root.geometry("600x180")
root.resizable(False, False)
root.title('Download images from web')

# store url web
url = tk.StringVar()


def download():
    """ callback when the login button clicked
    """
    print(f'You entered url: {url.get()}')
    ScrapeService.scrape_images_web(url.get().strip())


# Frame
main_frame = ttk.Frame(root)
main_frame.pack(padx=20, pady=20, fill='x', expand=True)


# URL
url_label = ttk.Label(main_frame, text="URL:")
url_label.pack(fill='x', expand=True)

url_entry = ttk.Entry(main_frame, textvariable=url)
url_entry.pack(fill='x', expand=True, ipadx=10, ipady=3)
url_entry.focus()


# get button
download_button = ttk.Button(
    main_frame, text="Download", command=download)
download_button.pack(fill='x', expand=True, pady=20, ipadx=10, ipady=3)

# RUN
root.mainloop()
