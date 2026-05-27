"""
Base factory using factory_boy + Faker.
Add one factory per entity — keeps test data creation consistent and DRY.

Usage:
    user = UserFactory()                    # unsaved instance
    user = UserFactory.create(db=db)        # saved to test DB

Example factory (uncomment and adapt when you have a User entity):

    import factory
    from faker import Faker
    from app.entity.user import User
    from app.enums.enums import UserRole
    from app.util.security import get_password_hash

    fake = Faker()

    class UserFactory(factory.Factory):
        class Meta:
            model = User

        full_name = factory.LazyFunction(fake.name)
        email     = factory.LazyFunction(fake.unique.email)
        password_hash = factory.LazyFunction(lambda: get_password_hash("password123"))
        role      = UserRole.USER
        is_active = True
"""
