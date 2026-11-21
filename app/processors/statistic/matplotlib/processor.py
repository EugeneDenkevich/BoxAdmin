from datetime import datetime, timezone
from io import BytesIO
from typing import Sequence
from uuid import UUID
from zoneinfo import ZoneInfo

from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from app.processors.statistic.protocol import StatisticProcessor
from app.schemas import PoolAttendanceVote


class MatplotlibProcessor(StatisticProcessor):
    def __init__(self, timezone_name: str) -> None:
        self.timezone = ZoneInfo(timezone_name)

    def get_statistic(self, votes: Sequence[PoolAttendanceVote]) -> bytes:
        attendance_by_pool: dict[UUID, tuple[datetime, int]] = {}

        for vote in votes:
            local_created_at = self._to_local_time(vote.created_at)
            created_at, count = attendance_by_pool.get(
                vote.pool_id,
                (local_created_at, 0),
            )

            if vote.option_ids is not None and 0 in vote.option_ids:
                count += 1

            attendance_by_pool[vote.pool_id] = (created_at, count)

        attendance = sorted(attendance_by_pool.values(), key=lambda item: item[0])
        attendance = attendance[-20:]

        figure = Figure(
            figsize=(10, 5.5),
            facecolor="#f8fafc",
            layout="constrained",
        )

        FigureCanvasAgg(figure)

        axis = figure.subplots()
        axis.set_facecolor("#f8fafc")
        axis.set_title(
            "Посещаемость по голосованиям",
            loc="left",
            fontsize=16,
            fontweight="bold",
            color="#0f172a",
            pad=16,
        )

        if attendance:
            self._draw_attendance(axis, attendance)
        else:
            axis.set_axis_off()
            axis.text(
                0.5,
                0.5,
                "Пока нет данных о голосованиях",
                ha="center",
                va="center",
                fontsize=13,
                color="#64748b",
                transform=axis.transAxes,
            )

        output = BytesIO()
        figure.savefig(output, format="png", dpi=160)

        return output.getvalue()

    def _draw_attendance(
        self,
        axis: Axes,
        attendance: list[tuple[datetime, int]],
    ) -> None:
        dates = [created_at.strftime("%d.%m.%Y") for created_at, _ in attendance]
        counts = [count for _, count in attendance]
        positions = list(range(len(attendance)))

        bars = axis.bar(
            positions,
            counts,
            width=0.68,
            color="#2563eb",
            edgecolor="#1d4ed8",
            linewidth=0.8,
            zorder=3,
        )

        axis.bar_label(
            bars,
            labels=[str(count) for count in counts],
            padding=4,
            fontsize=9,
            color="#0f172a",
        )

        average = sum(counts) / len(counts)
        axis.axhline(
            average,
            color="#f97316",
            linestyle="--",
            linewidth=1.6,
            label=f"Среднее: {average:.1f}",
            zorder=2,
        )

        axis.set_xticks(positions, dates)
        axis.tick_params(axis="x", labelrotation=35, labelsize=8)
        axis.set_ylabel("Голосов «иду»", color="#475569")
        axis.set_xlabel("Дата опроса", color="#475569")
        axis.yaxis.set_major_locator(MaxNLocator(integer=True))
        axis.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.3, zorder=0)
        axis.set_axisbelow(True)
        axis.margins(x=0.04, y=0.18)
        axis.legend(frameon=False, loc="upper right")

        for spine_name in ("top", "right"):
            axis.spines[spine_name].set_visible(False)

    def _to_local_time(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(self.timezone)
