import matplotlib.pyplot as plt
import base64, io, random
import seaborn as sns

def off_frame() -> None:
    plt.gca().spines["top"].set_visible(False)    
    plt.gca().spines["bottom"].set_visible(False)    
    plt.gca().spines["right"].set_visible(False)    
    plt.gca().spines["left"].set_visible(False)

def test(ask_title: str) -> None:
    # Создаем список значений
    vals = [10, 10, 80, 0, 10, 10, 80, 0]

    sub_titles = ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"]

    colors = random.choices(list(plt.cm.colors.cnames.keys()), k=len(vals))

    # Создаем горизонтальную диаграмму
    # plt.barh(sub_titles, vals)

    plt.figure(figsize=(10+len(vals)/10, len(vals)/1.2))
    
    for color, sub_title, val, v in zip(colors, sub_titles, vals, range(len(vals))):
        plt.text(val+1, v-0.1, val, color="indigo", fontsize=12)
        plt.barh(sub_title, val, color=color)
    
    plt.xlabel('%', fontsize=18)
    off_frame()
      

    # Настраиваем параметры диаграммы
    plt.title(f'Резальтаты опроса: {ask_title}', fontsize=18)

    # Отображаем диаграмму
    plt.show()
    

def get_base64_graph(log, ask_title: str, vals: list[int], sub_titles: list[str]) -> bytes:

    try:
        colors = random.choices(list(plt.cm.colors.cnames.keys()), k=len(vals))

        plt.figure(figsize=(10+len(vals)/10, len(vals)/1.2))
    
        for color, sub_title, val, v in zip(colors, sub_titles, vals, range(len(vals))):
            plt.text(val+1, v-0.1, val, color="indigo", fontsize=12)
            plt.barh(sub_title, val, color=color)
    
        plt.xlabel('%', fontsize=18)
        off_frame()
        
        plt.title(f'Резальтаты опроса: {ask_title}', fontsize=18)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # photobase = base64.b64decode(photo)
        return buffer.getvalue()
    except Exception as err:
        log.error(err)

    return None


if __name__ == "__main__":
    test("DD")
    # with open("h.png", "wb") as f:
        # f.write(get_base64_graph())