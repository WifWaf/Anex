from models import db
from models import License
from datetime import timedelta, datetime
from errors import Err, LogLevel, log
import definitions


class LicenseLookUp:
    @staticmethod
    def by_license_key(key):
        """
        Retrieves a license record from the database based on a given key.

        :param key: The `key` parameter is the license key that is used to retrieve a license from the
        database
        :return: The function `by_license_key` is returning the result of the query
        `License.query.get(str(key))`.
        """
        return License.query.get(str(key))


class LicenseManage:
    @staticmethod
    def create(uuid, days):
        """
        Creates a new license key with a given UUID and license duration

        :param uuid: The `uuid` parameter is a unique identifier for the license key. It is used to uniquely
        identify each license key in the system
        :param days: The "days" parameter represents the number of days until the license key expires. If
        the value of "days" is 0, it means the license key does not expire
        :return: the value of the variable `ret_id`.
        """
        log("New license key requested", LogLevel.INFO)

        can_expire = True
        if days == 0:
            can_expire = False

        expiration_date = datetime.now() + timedelta(days=days)
        ret_id = str(uuid)
        try:
            license = License(
                id=ret_id,
                status=definitions.STATUS_ACTIVE,
                can_expire=can_expire,
                expires=expiration_date,
                claimed=False,
            )
            db.session.add(license)

        except Exception as e:
            return Err.database_return(e)

        db.session.commit()
        return ret_id


class LicenseEntity:
    def __init__(self, key):
        """
        Initialises an object with properties based on a license key.

        :param key: The "key" parameter is used to identify a specific license in the License table. It is
        used to query the License table and retrieve the corresponding license row
        """
        lic_row = License.query.filter_by(id=str(key)).first()

        if lic_row is None:
            Err.client_return(Err.ERROR_MESSAGES['INVALID_LICENSE'], LogLevel.INFO)

        self.id = lic_row.id
        self.status = lic_row.status
        self.can_expire = lic_row.can_expire
        self.expires = lic_row.expires
        self.claimed = lic_row.claimed

    def update(self, key):
        """
        Updates the attributes of the license based on the values retrieved from a database
        query.

        :param key: The "key" parameter is a unique identifier used to retrieve a specific license from the
        database. It is used to query the License table and find the corresponding license row with the
        matching "id" value
        """
        lic_row = License.query.filter_by(id=str(key)).first()

        if lic_row is None:
            Err.client_return(Err.ERROR_MESSAGES['INVALID_LICENSE'], LogLevel.INFO)

        self.id = lic_row.id
        self.status = lic_row.status
        self.can_expire = lic_row.can_expire
        self.expires = lic_row.expires
        self.claimed = lic_row.claimed

    def commit(self):
        """
        Updates the fields of a License object and commits the changes to the database.
        """
        lic_row = License.query.filter_by(id=self.id).first()

        lic_row.id = self.id
        lic_row.status = self.status
        lic_row.can_expire = self.can_expire
        lic_row.expires = self.expires
        lic_row.claimed = self.claimed

        db.session.commit()

    def expired(self):
        """
        Checks if the current time is past the expiration time for the license and updates the status if
        necessary.
        :return: a boolean value. If the current datetime is greater than the value of `self.expires`, it
        will return `True`. Otherwise, it will return `False`.
        """
        if datetime.now() > self.expires:
            if self.status != definitions.STATUS_INACTIVE:
                self.status = definitions.STATUS_INACTIVE
                self.commit()
            return True
        return False
