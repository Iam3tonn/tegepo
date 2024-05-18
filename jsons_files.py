import time
from parsers import balisun, detik, expat, google_bali_en, google_bali_ru, google_news_indonesia, bisnis, cnbc, cnn, jawapos, infodenpasar, nusabali, tribunnews, kilasbali

def main():
    start_time = time.time()

    scripts_to_run = [
        balisun.run,
        detik.run,
        expat.run,
        google_bali_en.run,
        google_bali_ru.run,
        google_news_indonesia.run,
        bisnis.run,
        cnbc.run,
        cnn.run,
        jawapos.run,
        infodenpasar.run,
        nusabali.run,
        tribunnews.run,
        kilasbali.run
    ]

    for script in scripts_to_run:
        print(f"Выполнение {script.__name__}.py")
        try:
            script()
        except Exception as e:
            print(f"Ошибка при выполнении {script.__name__}.py: {e}")
        print(" ")

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Время выполнения программы: {execution_time:.2f} секунд")

if __name__ == "__main__":
    main()
