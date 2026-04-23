from __future__ import annotations
import math
import time
import random
from dataclasses import dataclass
from typing import List, Tuple



#1 Проєктування та реалізація імутабельних моделей даних

@dataclass(frozen=True)
class PolarPoint:
    radius: float
    angle: float

    @staticmethod
    def fromCartesian(p: CartesianPoint2D) -> "PolarPoint":
        radius = math.sqrt(p.x**2 + p.y**2)
        angle = math.atan2(p.y, p.x)
        return PolarPoint(radius, angle)


@dataclass(frozen=True)
class CartesianPoint2D:
    x: float
    y: float

    @staticmethod
    def fromPolar(p: PolarPoint) -> "CartesianPoint2D":
        x = p.radius * math.cos(p.angle)
        y = p.radius * math.sin(p.angle)
        return CartesianPoint2D(x, y)


@dataclass(frozen=True)
class SphericalPoint:
    radius: float
    azimuth: float
    polarAngle: float

    @staticmethod
    def fromCartesian(p: CartesianPoint3D) -> "SphericalPoint":
        radius = math.sqrt(p.x**2 + p.y**2 + p.z**2)
        azimuth = math.atan2(p.y, p.x)
        polarAngle = math.acos(p.z/radius) if radius != 0 else 0
        return SphericalPoint(radius, azimuth, polarAngle)


@dataclass(frozen=True)
class CartesianPoint3D:
    x: float
    y: float
    z: float

    @staticmethod
    def fromSpherical(p: SphericalPoint) -> "CartesianPoint3D":
        x = p.radius * math.sin(p.polarAngle) * math.cos(p.azimuth)
        y = p.radius * math.sin(p.polarAngle) * math.sin(p.azimuth)
        z = p.radius * math.cos(p.polarAngle)
        return CartesianPoint3D(x, y, z)



#2 Реалізація функцій для обчислення відстаней

def distance_2d_cartesian(p1: CartesianPoint2D, p2: CartesianPoint2D) -> float:
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

def distance_2d_polar(p1: PolarPoint, p2: PolarPoint) -> float:
    return math.sqrt(p1.radius**2 + p2.radius**2 - 2 * p1.radius * p2.radius * math.cos(p1.angle - p2.angle))

def distance_3d_cartesian(p1: CartesianPoint3D, p2: CartesianPoint3D) -> float:
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2 + (p2.z - p1.z) ** 2)

def distance_3d_spherical_chord(p1: SphericalPoint, p2: SphericalPoint) -> float:
    return math.sqrt(p1.radius ** 2 + p2.radius ** 2 - 2 * p1.radius * p2.radius * (
            math.sin(p1.polarAngle) * math.sin(p2.polarAngle) * math.cos(p1.azimuth - p2.azimuth) +
            math.cos(p1.polarAngle) * math.cos(p2.polarAngle)
    ))

def distance_3d_spherical_arc(p1: SphericalPoint, p2: SphericalPoint) -> float:
    return p1.radius * math.acos(
        math.sin(p1.polarAngle) * math.sin(p2.polarAngle) * math.cos(p1.azimuth - p2.azimuth) +
        math.cos(p1.polarAngle) * math.cos(p2.polarAngle)
    )



#3 Бенчмаркінг

def run_benchmarks():
    count = 100_000
    print(f"Запуск бенчмарків для {count} пар точок...\n")

    # 3.1. 2D Бенчмарк [cite: 91]
    polar_pairs = [(PolarPoint(random.uniform(1, 100), random.uniform(0, 2*math.pi)),
                    PolarPoint(random.uniform(1, 100), random.uniform(0, 2*math.pi))) for _ in range(count)]
    cartesian_pairs_2d = [(CartesianPoint2D.fromPolar(p1), CartesianPoint2D.fromPolar(p2)) for p1, p2 in polar_pairs]

    start = time.time()
    for p1, p2 in polar_pairs:
        distance_2d_polar(p1, p2)
    time_polar_2d = time.time() - start

    start = time.time()
    for p1, p2 in cartesian_pairs_2d:
        distance_2d_cartesian(p1, p2)
    time_cartesian_2d = time.time() - start

    # 3.2. 3D Бенчмарк [cite: 98]
    spherical_pairs = []
    for _ in range(count):
        r = random.uniform(1, 100)
        p1 = SphericalPoint(r, random.uniform(0, 2*math.pi), random.uniform(0, math.pi))
        p2 = SphericalPoint(r, random.uniform(0, 2*math.pi), random.uniform(0, math.pi))
        spherical_pairs.append((p1, p2))

    cartesian_pairs_3d = [(CartesianPoint3D.fromSpherical(p1), CartesianPoint3D.fromSpherical(p2)) for p1, p2 in spherical_pairs]

    start = time.time()
    for p1, p2 in spherical_pairs:
        distance_3d_spherical_chord(p1, p2)
    time_chord = time.time() - start

    start = time.time()
    for p1, p2 in spherical_pairs:
        distance_3d_spherical_arc(p1, p2)
    time_arc = time.time() - start

    start = time.time()
    for p1, p2 in cartesian_pairs_3d:
        distance_3d_cartesian(p1, p2)
    time_cartesian_3d = time.time() - start

    # Вивід результатів [cite: 122]
    print("| Підхід | Час виконання (сек) |")
    print("| :--- | :--- |")
    print(f"| 2D Полярна (теорема косинусів) | {time_polar_2d:.4f} |")
    print(f"| 2D Декартова (Евклід) | {time_cartesian_2d:.4f} |")
    print(f"| 3D Сферична (хорда) | {time_chord:.4f} |")
    print(f"| 3D Сферична (дуга) | {time_arc:.4f} |")
    print(f"| 3D Декартова (Евклід) | {time_cartesian_3d:.4f} |")


def test_conversions():
    print("--- Результати перевірки коректності ---")

    # Тест для 2D: Cartesian -> Polar -> Cartesian
    original_2d = CartesianPoint2D(10.0, -5.5)
    polar_temp = PolarPoint.fromCartesian(original_2d)
    result_2d = CartesianPoint2D.fromPolar(polar_temp)

    is_correct_2d = math.isclose(original_2d.x, result_2d.x, abs_tol=1e-9) and \
                    math.isclose(original_2d.y, result_2d.y, abs_tol=1e-9)

    print(f"2D тест: {original_2d} -> {result_2d}")
    print(f"Результат: {'УСПІШНО' if is_correct_2d else 'ПОМИЛКА'}")

    # Тест для 3D: Cartesian -> Spherical -> Cartesian
    original_3d = CartesianPoint3D(1.0, 2.0, 3.0)
    spherical_temp = SphericalPoint.fromCartesian(original_3d)
    result_3d = CartesianPoint3D.fromSpherical(spherical_temp)

    is_correct_3d = math.isclose(original_3d.x, result_3d.x, abs_tol=1e-9) and \
                    math.isclose(original_3d.y, result_3d.y, abs_tol=1e-9) and \
                    math.isclose(original_3d.z, result_3d.z, abs_tol=1e-9)

    print(f"3D тест: {original_3d} -> {result_3d}")
    print(f"Результат: {'УСПІШНО' if is_correct_3d else 'ПОМИЛКА'}\n")

if __name__ == "__main__":
    test_conversions()
    run_benchmarks()