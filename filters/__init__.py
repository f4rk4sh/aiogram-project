from loader import dp

from .permission import IsAdmin, IsMaster

if __name__ == "filters":
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsMaster)
