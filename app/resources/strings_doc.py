
"""
@apiDefine UserAlreadyExistsError
@apiError UserAlreadyExists A user for the provided properties already exists in the database. Maybe you should try to modify
instead of creating something new. Take a look at the put methods.
@apiErrorExample Error-Response:
    HTTP/1.1 404 Not Found
    {
        "message":"this user already exists"
    }
"""

"""
@apiDefine ResourceAlreadyExistsError
@apiError UserAlreadyExists A Resource for the provided properties (unique keys) already exists in the database. Maybe you should try to modify
instead of creating something new. Take a look at the put methods.
@apiErrorExample ResourceAlreadyExistsError:
    HTTP/1.1 404 Not Found
    {
        "message": "message that specifies the error"
    }
"""

"""
@apiDefine NoSuchResourceError
@apiError UserAlreadyExists No Resource for the provided properties (unique keys) exists in the database. You are trying t
o access a Resource object, possibly
 to update some information on it or some information that are associated with it. Therefor this resource must be present
  in the first place.
@apiErrorExample NoSuchResourceError:
    HTTP/1.1 404 Not Found
    {
        "message": "message that specifies the error"
    }
"""

"""
@apiDefine NoSuchUserError
@apiError NoSuchUserError There is no such user in the database. You are trying to access a user object, possibly
 to update some information on the user or some information that are associated with the user. Therefor a user object
  must be present in the first place.
@apiErrorExample NoSuchUserError:
    HTTP/1.1 404 Not Found
    {
        "message": "this user does not exist"
    }
"""

"""
@apiDefine BadRequest
@apiError BadRequest The provided arguments are not valid. Look at the specification, you might not have provided enough
fields in your request or you might not have provided a valid value for a field.
@apiErrorExample BadRequest:
    HTTP/1.1 400 Bad Request
    {
        "field_1": "error message for this field",
        "field_2": "error message for this field",
        "field_3": "..."
    }
"""

"""
@apiDefine CouldNotBeSavedError
@apiError CouldNotBeSavedError There was an internal server error. Saving your data was not successful.
@apiErrorExample CouldNotBeSavedError:
  HTTP/1.1 500 Internal Server Error
  {
    "message": "Error while saving"
  }
"""

"""
@apiDefine SuccessfullyCreated
@apiSuccess SuccessfulEmpty There were no errors, your request was successfully carried out. The resource was created.
@apiSuccessExample Success-Response:
  HTTP/1.1 201 OK
  {
    "message:""(user {user} added to group {group})+. ({key} set to {value})*"
    }
"""

"""
@apiDefine SuccessfullyDeleted
@apiSuccess SuccessfullyDeleted There were no errors, your request was successfully carried out. The resource was deleted.
@apiSuccessExample Success-Response:
  HTTP/1.1 201 OK
  {
    "message:" "resource deleted"
    }
"""