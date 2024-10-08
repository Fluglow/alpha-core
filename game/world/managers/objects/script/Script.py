import time
from game.world.managers.objects.script.ScriptCommand import ScriptCommand
from game.world.managers.objects.script.ConditionChecker import ConditionChecker
from utils.Logger import Logger


class Script:
    def __init__(self, script_id, db_commands, source, target, script_handler, delay=0.0, event=None):
        self.id: int = script_id
        self.commands: list[ScriptCommand] = [ScriptCommand(self, command) for command in db_commands]
        self.source = source
        self.target = target
        self.script_handler = script_handler
        self.event = event
        self.delay: float = delay
        self.time_added: float = time.time()  # Time start reference for this script execution.
        self.start_time: float = 0.0  # Time start reference for embedded ScriptCommands execution.
        self.started = False
        self.aborted = False

    def __hash__(self):
        return self.id

    def update(self, now):
        if not self.started:
            # Check initial delay for command sequence.
            if self.delay and now - self.time_added < self.delay:
                return
            self.start_time = now
            self.started = True

        for script_command in list(self.commands):
            # Stop looping if script has been aborted externally.
            if self.aborted:
                return

            # Check if it's time to execute the command action.
            if script_command.delay and now - self.start_time < script_command.delay:
                continue

            self.commands.remove(script_command)

            # Try to resolve initial targets for this command.
            succeed, source, target = script_command.resolve_initial_targets(self.source, self.target)
            if not succeed:
                continue

            # Try to resolve the final targets for this command.
            succeed, source, target = script_command.resolve_final_targets(self.source, self.target)
            if not succeed:
                continue

            script_command.source = source
            script_command.target = target

            # Check if source or target are currently in inactive cells, if so, make their cells become active.
            if source and not source.get_map().is_active_cell(source.current_cell):
                source.get_map().activate_cell_by_world_object(source)
            if target and target != source and not target.get_map().is_active_cell(target.current_cell):
                target.get_map().activate_cell_by_world_object(target)

            # Condition is not met, skip.
            if not ConditionChecker.validate(script_command.condition_id, source=self.source, target=self.target):
                continue

            # Execute action.
            should_abort = self.script_handler.handle_script_command_execution(script_command)
            if should_abort:
                self.abort()
                return

    def abort(self):
        event_info = {self.event.get_event_info() if self.event else 'None'}
        Logger.warning(f'Script {self.id} from event {event_info}, Aborted.')
        self.aborted = True
        self.commands.clear()

    def is_complete(self):
        return not self.commands or self.aborted
