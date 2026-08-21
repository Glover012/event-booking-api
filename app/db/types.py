from sqlalchemy import String, TypeDecorator

from ..core.security import HashedPassword


# TypeDecorator allows to convert data type in both directions
# so into the database and from database
# Additionally, like in this example it gives an opportunity
# to validate the data before it reaches the database
# In case of password, we always expect HashedPassword Instance
# The db must never recieve non hashed password, therefore this part
# protects from such situations, especially when the code in 
# other parts of application will be changing
class HashedPasswordType(TypeDecorator):
    """
    Stores a HashedPassword as text and refuses anything else.

    This is the barrier no ORM path can bypass - SQLAlchemy runs the bind
    processor on every write, so a plaintext password cannot reach the
    column. Raw SQL skips it, but such a row will raise an error on the first 
    read due to HashedPassword class constructor.

    hashed_password column is NOT NULL, therefore None raises an error
    """

    impl = String # Represent column type in the db - VARCHAR

    # Allows SQLAlchemy to cache compiled statements that use this column.
    # Safe here, since this type takes no arguments and always behaves
    # the same way
    cache_ok = True

    # Direction: Python -> Database
    # It confirms correct type and unpacks the data
    # Raise TypeError when data isn't HashedPassword instance
    ## dialect allows to change behavior between different databases
    ## example: postgres and sqlite3, unused here
    def process_bind_param(self, value, dialect) -> str:
        if not isinstance(value, HashedPassword):
            raise TypeError(
                f"hashed_password accepts only HashedPassword instances, "
                f"got {type(value).__name__}"
            )

        # HashedPassword is a SecretStr, so the value has to be unwrapped
        return value.get_secret_value()

    # Direction: Database -> Python
    # Instantiate value received from db, back into HashedPassword
    def process_result_value(self, value, dialect) -> HashedPassword:
        return HashedPassword(value)
