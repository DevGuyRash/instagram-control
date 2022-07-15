

class UserInput:

    def __init__(self):
        pass

    @staticmethod
    def get_input(valid_options: [list, set, dict],
                  valid_type: type = None,
                  ) -> any:
        """
        Gets valid user input that must be within `valid_options`.

        Checks that user input is of type `valid_type` if it's provided,
        attempting to convert user input to this type. Then checks that
        user input is in `valid_options`. Prompts for input on failure
        of either condition, using recursion.

        Args:
            valid_options: Valid input options for the user to select
                from.
            valid_type: Type that user input must match.

        Returns:
            Valid user input that within `valid_options` and is of type
            `valid_type` if it was provided.
        """
        # Make options case-insensitive, and able to have spaces
        valid_options = {str(option).casefold()
                         for option in valid_options}
        # Store user input in another var to convert it to valid_type if it's
        # provided.
        retval = user_input = input()
        if valid_type:
            try:
                retval = valid_type(user_input)
            except ValueError:
                user_input_type = type(user_input)
                print(f"Invalid type given!")
                print(f"Input type "
                      f"given: {user_input_type}. Input type required: {valid_type}.")
                print("Please try again: ", end='')
                return UserInput.get_input(valid_options, valid_type)

        if user_input not in valid_options:
            print("Invalid selection! Please try again: ", end='')
            return UserInput.get_input(valid_options)

        return retval

    @staticmethod
    def create_menu(menu: [list, set, dict], exit_: bool = False) -> any:
        """
        Prints `menu` in a numbered format and gets valid user input.

        Enumerates `menu` and prints out all options in the form of:
        1. Option
        2. Option
        3. Option

        Will only accept a valid number selection, and return the user
        selected option associated with that number.

        Args:
            menu: Options for user to choose from.
            exit_: When `True`, adds an "exit" option

        Returns:
            User selected option from `menu`.
        """
        menu_list = {index + 1: value for index, value in enumerate(menu)}
        # Create exit_ menu option if True
        if exit_:
            menu_list.update({len(menu_list) + 1: "exit"})

        # Print out menu
        for index, item in menu_list.items():
            print(f"{index}. {item}")

        print("Please type a number from the selection above: ", end='')
        # Get user input and return their choice
        user_choice = UserInput.get_input(menu_list, valid_type=int)
        return menu_list[user_choice]





