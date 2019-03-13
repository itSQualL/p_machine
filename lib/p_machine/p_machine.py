class PMachine():
    def __init__(self, initial_state):
        self.initial_state = initial_state

    def run(self):
        print("Starting PMachine...")
        current_state = self.initial_state

        while current_state != None:
            current_state.run()
            current_state = current_state.next()

        return True
