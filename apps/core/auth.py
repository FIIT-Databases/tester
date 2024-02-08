import logging
from typing import TypedDict, Dict, Optional

import ldap
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User, Group
from django.utils import timezone

from apps.core.models import AuthSource


class LdapBackend(ModelBackend):
    class Config(TypedDict):
        URI: str
        ROOT_DN: str
        BIND: str
        USER_ATTR_MAP: Dict[str, str]
        GROUP_MAP: Dict[str, str]
        FILTER: str

    def _ldap(self, username: str, password: str, auth_source: AuthSource) -> Optional[User]:
        config: LdapBackend.Config = auth_source.content
        connection = ldap.initialize(uri=config["URI"])
        connection.set_option(ldap.OPT_REFERRALS, 0)

        try:
            connection.simple_bind_s(config["BIND"].format(username=username), password)
        except ldap.LDAPError as e:
            logging.warning(
                f"Unable to bind with external service (id={auth_source.pk}, name={auth_source.name}): {e}"
            )
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(
                username=username,
            )
            user.set_unusable_password()

        result = connection.search(
            f"{config['ROOT_DN']}", ldap.SCOPE_SUBTREE, config["FILTER"].format(username=username), ["*"]
        )

        user_type, profiles = connection.result(result, 60)

        if profiles:
            name, attrs = profiles[0]

            # LDAP properties
            for model_property, ldap_property in config["USER_ATTR_MAP"].items():
                setattr(user, model_property, attrs[ldap_property][0].decode())

            user.last_login = timezone.now()
            user.save()

            # LDAP groups
            user.groups.clear()
            for ldap_group in attrs.get("memberOf", []):
                if ldap_group.decode() in config["GROUP_MAP"]:
                    try:
                        group = Group.objects.get(name=config["GROUP_MAP"][ldap_group.decode()])
                    except Group.DoesNotExist:
                        continue
                    user.groups.add(group)
        else:
            logging.warning(
                f"Could not find user profile for {username} in auth source {auth_source.name}"
                f" (id={auth_source.pk}, name={auth_source.name})"
            )
            return None

        connection.unbind()

        user.save()

        return user

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None

        for auth_source in AuthSource.objects.filter(is_active=True):
            logging.debug(f"Checking {auth_source.name}")
            if auth_source.driver == AuthSource.Driver.LDAP:
                user = self._ldap(username, password, auth_source)

            if user:
                break

        return user
