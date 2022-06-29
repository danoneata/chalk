from __future__ import annotations

from functools import reduce
from typing import Callable, Iterable

from planar import Affine, BoundingBox, Point, Polygon, Vec2, Vec2Array

from chalk.transform import (
    Transformable,
    apply_affine,
    remove_translation,
    transpose_translation,
)

SignedDistance = float

unit_x = Vec2(1, 0)
unit_y = Vec2(0, 1)


class Envelope(Transformable):
    def __init__(
        self, f: Callable[[Vec2], SignedDistance], is_empty: bool = False
    ) -> None:
        self.f = f
        self.is_empty = is_empty

    def __call__(self, direction: Vec2) -> SignedDistance:
        assert not self.is_empty
        return self.f(direction)

    def __add__(self, other: Envelope) -> Envelope:
        if self.is_empty:
            return other
        if other.is_empty:
            return self
        return Envelope(
            lambda direction: max(self(direction), other(direction))
        )

    @property
    def center(self) -> Point:
        assert not self.is_empty
        return Point(
            (-self(-unit_x) + self(unit_x)) / 2,
            (-self(-unit_y) + self(unit_y)) / 2,
        )

    @property
    def width(self) -> float:
        assert not self.is_empty
        return self(unit_x) + self(-unit_x)

    @property
    def height(self) -> float:
        assert not self.is_empty
        return self(unit_y) + self(-unit_y)

    @staticmethod
    def mappend(envelope1: Envelope, envelope2: Envelope) -> Envelope:
        return envelope1 + envelope2

    @staticmethod
    def empty() -> Envelope:
        return Envelope(lambda v: 0, is_empty=True)

    @staticmethod
    def concat(envelopes: Iterable[Envelope]) -> Envelope:
        return reduce(Envelope.mappend, envelopes, Envelope.empty())

    def apply_transform(self, t: Affine) -> Envelope:  # type: ignore
        if self.is_empty:
            return self
        _, _, c, _, _, f = t[:6]
        u = Vec2(c, f)
        t1 = transpose_translation(remove_translation(t))

        def wrapped(v: Vec2) -> SignedDistance:
            t1v = apply_affine(t1, v)
            t1v2 = t1v.scaled_to(1)
            return self(t1v2) * t1v.length + u.dot(v) / (v.dot(v))  # type: ignore

        return Envelope(wrapped)

    def envelope_v(self, v: Vec2) -> Vec2:
        if self.is_empty:
            return Vec2(0, 0)
        v = v.scaled_to(1)
        d = self(v)
        return d * v

    @staticmethod
    def from_bounding_box(box: BoundingBox) -> Envelope:
        def wrapped(d: Vec2) -> SignedDistance:
            v: float = apply_affine(
                Affine.rotation(d.angle), box
            ).bounding_box.max_point.x
            return v / d.length  # type: ignore

        return Envelope(wrapped)

    @staticmethod
    def from_circle(radius: float) -> Envelope:
        def wrapped(d: Vec2) -> SignedDistance:
            return radius / d.length  # type: ignore

        return Envelope(wrapped)

    @staticmethod
    def from_path(path: Vec2Array) -> Envelope:
        if len(path) > 2:
            hull = Polygon.convex_hull(path)

            def wrapped(d: Vec2) -> SignedDistance:
                v: float = apply_affine(
                    Affine.rotation(d.angle), hull
                ).bounding_box.max_point.x
                return v / d.length  # type: ignore

            return Envelope(wrapped)
        else:
            return Envelope.from_bounding_box(BoundingBox(path))

    def to_path(self) -> Vec2Array:
        "Draws an envelope by sampling every 10 degrees."
        pts = []
        for i in range(0, 361, 10):
            v = Vec2.polar(i)
            pts.append(self(v) * v)
        return Vec2Array(pts)