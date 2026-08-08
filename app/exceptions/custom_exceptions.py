class FileNotFoundException(Exception):
    def __init__(self):
        self.message = "File not found"
        super().__init__(self.message)


class PermissionDeniedException(Exception):
    def __init__(self):
        self.message = "You do not have permission to perform this action"
        super().__init__(self.message)


class DuplicateUserException(Exception):
    def __init__(self):
        self.message = "Username or email already exists"
        super().__init__(self.message)


class InvalidCredentialsException(Exception):
    def __init__(self):
        self.message = "Invalid email or password"
        super().__init__(self.message)


class InvalidFileNameException(Exception):
    def __init__(self):
        self.message = "Invalid file name"
        super().__init__(self.message)