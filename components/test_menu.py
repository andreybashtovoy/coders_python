from components.menu import Menu


class TestMenu(Menu):
    def __init__(self, updater):
        super().__init__(updater, 'components/user_stats/user_stats.xml', 'test_stats')
