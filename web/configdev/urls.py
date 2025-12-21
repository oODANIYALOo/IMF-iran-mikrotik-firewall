from django.urls import path
from configdev.views import AddAndDeleteMikrotickViewe,ConfigMikrotick,CheckMikrotick,IndexView,MikrotikCustomConfigView

app_name = "configdev"
urlpatterns = [
    path("",IndexView.as_view(), name="index"),
    path("add_dell/", AddAndDeleteMikrotickViewe.as_view(), name="add_dell"),
    path("conifig_mikrotick/", ConfigMikrotick.as_view(), name="config_mikrotick"),
    path("check/", CheckMikrotick.as_view(), name="check"),
    path("mikrotick_custom_config/", MikrotikCustomConfigView.as_view(), name="mikrotick_custom_config"),


]
