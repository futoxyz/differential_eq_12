from dataclasses import dataclass, replace
import numpy as np
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class Parameters:
    a: float
    b0: float
    k: float
    sigma: float
    g: float
    H: float

    def __post_init__(self):
        for name in ("a", "b0", "sigma", "g", "H"):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} должен быть конечным и > 0")
        if not np.isfinite(self.k):
            raise ValueError("k должен быть конечным")

    @property
    def A(self):
        return self.sigma * np.sqrt(2 * self.g) / (self.a * self.b0)

    @property
    def p(self):
        return self.k + 0.5


def emptying_time(m):
    if m.p <= 0:
        return np.inf
    return m.H**m.p / (m.p * m.A)


def volume(m):
    """ Начальный объём. При k <= -1 интеграл расходится """
    if m.k <= -1:
        return np.inf
    return m.a * m.b0 * m.H**(m.k + 1) / (m.k + 1)


def height(t, m) -> np.array:
    """ Явное решение h(t) """
    t = np.asarray(t, dtype=float)
    if np.any(~np.isfinite(t)) or np.any(t < 0):
        raise ValueError("Время должно быть конечным и неотрицательным")

    p = m.p
    if p == 0:
        return m.H * np.exp(-m.A * t)
    x = -p * m.A * t / m.H**p
    if p > 0:
        T = emptying_time(m)
        active = t < T
        safe_x = np.where(active, x, 0.0)
        with np.errstate(divide="ignore"):
            values = m.H * np.exp(np.log1p(safe_x) / p)
        return np.where(active, values, 0.0)

    return m.H * np.exp(np.log1p(x) / p)


def time_at_height(h, m):
    """ Обратная зависимость t(h), 0 <= h <= H """
    h = np.asarray(h, dtype=float)
    if np.any(~np.isfinite(h)) or np.any((h < 0) | (h > m.H)):
        raise ValueError("Высота должна принадлежать [0, H]")
    positive = h > 0
    safe_h = np.where(positive, h, m.H)
    log_ratio = np.log(safe_h / m.H)
    if m.p == 0:
        values = -log_ratio / m.A
    else:
        values = (
            -m.H**m.p
            * np.expm1(m.p * log_ratio)
            / (m.p * m.A)
        )
    return np.where(positive, values, emptying_time(m))


def level_derivative(h, m):
    """ Правая часть ОДУ """
    h = np.asarray(h, dtype=float)
    if np.any(~np.isfinite(h)) or np.any(h <= 0):
        raise ValueError("Для вычисления h' требуется h > 0")
    return -m.A * h**(0.5 - m.k)


def print_results(models: tuple[Parameters]):
    print(f"{'k':>8} {'b0':>12} {'V, м³':>14} {'T, с':>14}")
    print("-" * 52)

    for m in models:
        T = emptying_time(m)
        V = volume(m)
        t_text = f"{T:.6f}"
        v_text = f"{V:.6f}"
        print(f"{m.k:8g} {m.b0:12.6g} {v_text:>14} {t_text:>14}")

def check_solutions(models: tuple[Parameters]):
    """ Численные проверки """
    for m in models:
        np.testing.assert_allclose(height(0.0, m), m.H)
        T = emptying_time(m)
        scale = m.H**m.p / m.A
        end = 0.8 * T if np.isfinite(T) else 2.0 * scale
        ts = np.linspace(0.05 * end, end, 30)
        hs = height(ts, m)
        np.testing.assert_allclose(
            time_at_height(hs, m), ts, rtol=1e-9, atol=1e-9
        )
        dt = end * 1e-5
        numerical_derivative = (
            height(ts + dt, m) - height(ts - dt, m)
        ) / (2 * dt)
        np.testing.assert_allclose(
            numerical_derivative,
            level_derivative(hs, m),
            rtol=1e-5,
            atol=1e-9,
        )
        assert np.all(np.diff(hs) < 0)
        if np.isfinite(T):
            np.testing.assert_allclose(height([T, 1.1 * T], m), 0.0)


def plot_results(models: tuple[Parameters]):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    ax1, ax2, ax3, ax4 = axes.flat
    finite_times = [
        emptying_time(m)
        for m in models
        if np.isfinite(emptying_time(m))
    ]
    fallback = max(m.H**m.p / m.A for m in models)
    horizon = 1.15 * max(finite_times, default=fallback)
    ts = np.linspace(0.0, horizon, 700)
    for m in models:
        ax1.plot(ts, height(ts, m), label=f"k = {m.k:g}")
    ax1.set(
        title="Уровень воды для разных форм",
        xlabel="t, с",
        ylabel="h, м",
    )

    base = next((m for m in models if m.k == 1.0), models[0])
    for factor in (0.5, 1.0, 1.5, 2.0):
        m = replace(base, H=factor * base.H)
        T = emptying_time(m)
        end = T if np.isfinite(T) else 3 * m.H**m.p / m.A
        times = np.linspace(0.0, end, 500)
        ax2.plot(times, height(times, m), label=f"H = {m.H:g} м")
    ax2.set(
        title=f"Один сосуд: k = {base.k:g}, b₀ фиксирован",
        xlabel="t, с",
        ylabel="h, м",
    )

    for m in models:
        lower = 0.0 if m.p > 0 else 0.01 * m.H
        hs = np.linspace(lower, m.H, 500)
        ax3.plot(hs, time_at_height(hs, m), label=f"k = {m.k:g}")
    ax3.set(
        title="Обратная зависимость t(h)",
        xlabel="h, м",
        ylabel="t, с",
    )

    heights = np.linspace(0.05 * base.H, 2 * base.H, 400)
    for m in models:
        if m.p > 0:
            times = heights**m.p / (m.p * m.A)
            ax4.plot(heights, times, label=f"k = {m.k:g}")
    ax4.set(
        title="T(H) при фиксированном b₀; k > −1/2",
        xlabel="H, м",
        ylabel="T, с",
    )
    for ax in axes.flat:
        ax.grid(True, alpha=0.3)
        ax.legend()
    fig.tight_layout()
    plt.show()