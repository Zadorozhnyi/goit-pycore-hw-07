from collections import UserDict
from datetime import datetime, timedelta

# Decorator for error handling
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This contact does not exist"
        except ValueError as err:
            return err.args[0]
        except IndexError:
            return "Enter the argument for the command"
    return inner


# Base class Field
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


# Class for storing and validation birthday
class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        try:
            self.value = datetime.strptime(self.value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


# Class to store name
class Name(Field):
    pass


# Class for storing and validation phone number
class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not self.value.isdigit() or len(self.value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")


# Class for storing records
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone_number, new_phone_number):
        phone_to_edit = self.find_phone(old_phone_number)
        if phone_to_edit:
            self.phones.remove(phone_to_edit)
            self.add_phone(new_phone_number)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = ', '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


# Class for work with address book
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_week = today + timedelta(days=7)
        result = []

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)

                # If the birthday already passed this year, check next year
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                # Check if birthday is within the next 7 days
                if today <= birthday_this_year <= upcoming_week:
                    # If birthday falls on a weekend, postpone to next Monday
                    if birthday_this_year.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))

                    result.append({
                        'name': record.name.value,
                        'birthday': birthday_this_year.strftime("%d.%m.%Y")
                    })

        return result

# CLI Functions
@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


@input_error
def add_contact(args, address_book: AddressBook):
    name, phone, *_ = args
    record = address_book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        address_book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_contact(args, address_book: AddressBook):
    # TODO Add the ability to change more than one phone number!
    name, phone = args
    record = address_book.find(name)
    if record:
        # Editing only first phone!
        record.edit_phone(record.phones[0].value, phone)
        return f"Contact '{name}' updated."
    raise KeyError


@input_error
def show_phone(args, address_book: AddressBook):
    name = args[0]
    record = address_book.find(name)
    if record:
        return f"Phone for '{name}': {', '.join([p.value for p in record.phones])}"
    raise KeyError


@input_error
def add_birthday(args, address_book: AddressBook):
    name, birthday = args
    record = address_book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for '{name}' added/updated."
    raise KeyError


@input_error
def show_birthday(args, address_book: AddressBook):
    name = args[0]
    record = address_book.find(name)
    if record and record.birthday:
        return f"Birthday for '{name}': {record.birthday}"
    raise KeyError


@input_error
def birthdays(address_book: AddressBook):
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        result = "\n".join([f"{contact['name']} - {contact['birthday']}" for contact in upcoming_birthdays])
        return f"Upcoming birthdays:\n{result}"
    return "No upcoming birthdays in the next 7 days."


@input_error
def show_all(address_book: AddressBook):
    if address_book:
        result = "\n".join([f"{name}: {', '.join([p.value for p in record.phones])}" for name, record in address_book.items()])
        return f"All contacts:\n{result}"
    return "No contacts found"


def main():
    address_book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, address_book))
        elif command == "change":
            print(change_contact(args, address_book))
        elif command == "phone":
            print(show_phone(args, address_book))
        elif command == "all":
            print(show_all(address_book))
        elif command == "add-birthday":
            print(add_birthday(args, address_book))
        elif command == "show-birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(birthdays(address_book))
        else:
            print("Invalid command.")


# Start the main function
if __name__ == "__main__":
    main()
