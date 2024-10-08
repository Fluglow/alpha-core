from game.world.managers.objects.gameobjects.GameObjectManager import GameObjectManager


class SpellFocusManager(GameObjectManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spell_focus_type = 0
        self.radius = 0
        self.linked_trap = 0

    # override
    def initialize_from_gameobject_template(self, gobject_template):
        super().initialize_from_gameobject_template(gobject_template)
        self.spell_focus_type = self.get_data_field(0, int)
        self.radius = self.get_data_field(1, float) / 2.0
        self.linked_trap = self.get_data_field(2, int)

    # override
    def use(self, player=None, target=None, from_script=False):
        if player and self.linked_trap:
            self.trigger_linked_trap(self.linked_trap, player, self.radius)
        super().use(player, target, from_script)
