"""Focus!

An application to help you with focusing (and resting).

Start the focused time!
Earn break time!
Rest!

Tasks

- Store history (I can use sqlite)
- Ruff plugins
- What can I add to ruff?
- ¿Qué pasa si pauso sin arrancar?
- Desactivar el botón de pausa si no ha arrancado.
- Show in real time the total focused time and the total break time.
- Add a README.
- Arreglar que quedó en negativo cuando pausé.
- Arreglar que no se ve el rojo cuando ejecuto.
- Fix the earned break time.
- Refactor again. (Clean unused timer interface)
- Original color is not black for main ticker.
- Gamify
- Upload to github.
- Type of works
- Add stop button (menú?).
- Skills (my idea of gamification).
- Another refactor.
- Experience.
- Sound? Tic tac might work.
- Split other classes to other files.
- Set goals? (sometimes, must switch between goals.)
- Create an installable app.
- Notifications?
- Increase size of button.
- Labels for "type of work".
- Use sqlite to store between sessions.
- Use a src directory structure.
- tox?
- Use red if balance is negative.
- Add ticker sound?
- Add experience (some way of grinding)
- Parametrize labels.
- How can I count/handle interruptions? Can read, can think.
- Add keyboard shortcuts.
- Make the ratio configurable.
- Prizes for everyday usage. Habits ??
- Restart the label to 00:00 when switching. (a minor visual improvement)
- Handle interruptions? What is an interruption? How can the be handled? Counted?
- Show watch in notifications area.
- Show in red if balance negative (earned_time_label).
- Store session: how?
- Define principles (for example, sensible defaults, and, also, )
- Show in red, when balance is negative (every second we can check)
- add a version (0.0.1)
- Subir a github.
- Hacer más grande el botón de concentrase y descansar (será buena idea?)
- Actualizar en tiempo real lo que va pasando.
- Adicionar una meta.
- Mostrar notificaciones.
- Pestañas para lo que quiero.
- Definir (con IA), qué estadísticas quiero almacenar.
- El README con fotos.
- Tests to test file.
- En lugar de minutes, mostrar minute si solo hay un minuto de descanso ganado.
- ¿Cómo organizar mejor estas tareas? En un archivo.
- If history is stored, can the session be restored?
- Todo lists?
- Si está pausado y se da en Focus!, despausar.
- Handle more than 99 minutes in clock.
- File with wishlist.
- Where to store config?
- Add a pre-commit.
- Add documentation.
- Add mypy.

"""

import asyncio

import toga
from toga.style.pack import CENTER, COLUMN, ROW, Pack

from focus import Focus
from timer import duration_from_seconds


class FocusApp(toga.App):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.focus_app = Focus()

        self._counting_task: asyncio.Task | None = None

    def startup(self) -> None:
        self.main_window = toga.Window()
        main_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=10))
        button_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding=10))

        self.timer_label = toga.Label(
            "00:00",
            style=Pack(
                padding=10,
                alignment=CENTER,
                font_size=150,
                display="pack",
                direction="column",
                text_align=CENTER,
            ),
        )
        main_box.add(self.timer_label)

        self.pause_button = toga.Button(
            "Pause",
            on_press=self.toggle_pause,
            style=Pack(padding=10, alignment=CENTER),
        )

        self.start_button = toga.Button(
            "Focus!",
            on_press=self.toggle_timers,
            style=Pack(padding=10, alignment=CENTER),
        )
        button_box.add(self.pause_button)
        button_box.add(self.start_button)
        main_box.add(button_box)

        self.total_focused_time_label = toga.Label(
            "Total focused time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        main_box.add(self.total_focused_time_label)
        self.total_break_time_label = toga.Label(
            "Total break time: 00:00", style=Pack(padding=10, alignment=CENTER)
        )
        main_box.add(self.total_break_time_label)

        self.earned_break_time_label = toga.Label(
            "Earned break time: 0 minutes", style=Pack(padding=10, alignment=CENTER)
        )
        main_box.add(self.earned_break_time_label)

        self.main_window.content = main_box
        self.main_window.show()

        self._counting_task = asyncio.create_task(self._update_timers())

    def toggle_pause(self, widget) -> None:
        if self.focus_app.paused:
            self.focus_app.unpause()
        else:
            self.focus_app.pause()

    def toggle_timers(self, widget) -> None:
        if not self.focus_app.started or self.focus_app.resting:
            self.focus_app.focus()
            self.earned_break_time_label.text = (
                f"Earned break time: {self.focus_app.earned_break_time // 60} minutes"
            )
            self.start_button.text = "Break"

            if self.focus_app.earned_break_time < 0:
                self.timer_label.style.color = "red"
        else:
            self.focus_app.rest()

            self.total_focused_time_label.text = f"Total focused time: {duration_from_seconds(self.focus_app.get_total_focused_seconds())}"
            self.earned_break_time_label.text = (
                f"Earned break time: {self.focus_app.earned_break_time // 60} minutes"
            )
            self.total_break_time_label.text = f"Total break time: {duration_from_seconds(self.focus_app.get_total_rested_seconds())}"
            self.start_button.text = "Focus!"

    async def _update_timers(self):
        """Updates the timer labels every second."""
        while True:
            if self.focus_app.paused:
                await asyncio.sleep(1)
                continue

            minutes, seconds = duration_from_seconds(
                self.focus_app.get_current_clock_time()
            )
            current_break_time = 0
            if self.focus_app.focusing:
                self.timer_label.style.color = "black"
                self.earned_break_time_label.text = f"Earned break time: {(self.focus_app.earned_break_time + self.focus_app.get_current_clock_time() // self.focus_app.focus_break_ratio) // 60} minutes"
                self.timer_label.text = str(
                    duration_from_seconds(self.focus_app.get_current_clock_time())
                )
                self.total_focused_time_label.text = f"Total focused time: {duration_from_seconds(self.focus_app.get_total_focused_seconds())}"
            else:
                current_break_time += self.focus_app.get_current_clock_time()

                self.earned_break_time_label.text = f"Earned break time: {(self.focus_app.earned_break_time - self.focus_app.get_current_clock_time()) // 60} minutes"
                self.timer_label.text = str(
                    duration_from_seconds(self.focus_app.get_current_clock_time())
                )
                self.total_break_time_label.text = f"Total break time: {duration_from_seconds(self.focus_app.get_total_rested_seconds())}"

            if (self.focus_app.earned_break_time - current_break_time) < 0:
                if self.focus_app.resting:
                    self.timer_label.style.color = "red"
                else:
                    self.timer_label.style.color = "black"
                self.total_break_time_label.color = "red"
            else:
                self.timer_label.style.color = "black"
                self.total_break_time_label.color = "black"

            await asyncio.sleep(1)


def main():
    return FocusApp("Focus!", "org.beeware.tutorial")


if __name__ == "__main__":
    main().main_loop()
