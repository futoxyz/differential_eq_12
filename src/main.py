from src.model import Parameters, print_results, check_solutions, plot_results
from src.constants import a, H, B, sigma, g


def main():
    ks: tuple[float] = (-0.75, -0.5, 0.0, 0.5, 1.0, 2.0)
    models = [
        Parameters(
            a=a,
            b0=B / H**k,
            k=k,
            sigma=sigma,
            g=g,
            H=H,
        )
        for k in ks
    ]

    print_results(models) # Таблица решений от k
    check_solutions(models) # Проверка решений
    plot_results(models) # Построение графиков


if __name__ == "__main__":
    main()