

# centers top level info widget
def center_top_level(instance):
    # window position to center
    instance.master.update_idletasks()

    x = instance.master.winfo_x()
    y = instance.master.winfo_y()
    mw = instance.master.winfo_width()
    mh = instance.master.winfo_height()

    w = instance.winfo_width()
    h = instance.winfo_height()

    mid_w = ((mw - w) // 2) + x
    mid_h = ((mh - h) // 2) + y

    instance.geometry("%dx%d+%d+%d" % (w, h, mid_w, mid_h))