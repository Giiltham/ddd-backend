# Projet Domain Driven Design ESGI

## CRUD permissions
| Role        | Resource             | Methods / Access             |
| ----------- | -------------------- | ---------------------------- |
| **Admin**   | All                  | Full access to all endpoints |
| **Manager** | **User**             | GET (self), PATCH (self)     |
|             | **Artists**          | GET (his artists)            |
|             | **Charts**           | GET                          |
|             | **Chart entries**    | GET                          |
|             | **Country**          | GET                          |
|             | **Country clusters** | GET                          |
| **Artist**  | **User**             | GET (self), PATCH (self)     |
|             | **Artists**          | GET (self), PATCH (self)     |
|             | **Charts**           | GET                          |
|             | **Chart entries**    | GET                          |
|             | **Country**          | GET                          |

## Custom endpoints access

### Admin

### Manager

### Artist