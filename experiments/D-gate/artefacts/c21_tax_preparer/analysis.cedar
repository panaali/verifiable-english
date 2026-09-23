@id("AliceView")
permit(
  principal == Taxpreparer::Professional::"Alice",
  action == Taxpreparer::Action::"viewDocument",
  resource == Taxpreparer::Document::"DEF"
);

permit(
  principal,
  action == Taxpreparer::Action::"viewDocument",
  resource
) when {
  principal.assigned_orgs.contains({location: resource.location, organization: resource.owner.organization, serviceline: resource.serviceline})
};

forbid(
  principal,
  action == Taxpreparer::Action::"viewDocument",
  resource
) when {
  !((context.consent.client == resource.owner) && context.consent.team_region_list.contains(principal.location))
};
