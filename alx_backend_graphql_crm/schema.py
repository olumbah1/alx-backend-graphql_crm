import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query)


class Query(CRMQuery, graphene.ObjectType):
    # Inherit CRM queries
    pass


class Mutation(CRMMutation, graphene.ObjectType):
    # Inherit CRM mutations
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)