# to run the test application
from application import Main

if __name__ == "__main__":
    main = Main(
        data_path = r"data",
        confidence_threshold=0.85)
    main.mainloop()

