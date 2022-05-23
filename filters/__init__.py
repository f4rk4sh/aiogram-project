from .permission import IsAdmin, IsMaster
from loader import dp


if __name__ == 'filters':
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsMaster)
