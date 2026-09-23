@createPolicyWhen("Create a template linked policy\n                   when a external user is added to a prez as viewer")
@id("BobView")
permit(
  principal == User::"Bob",
  action in [Action::"ExternalPrezViewActions"],
  resource == Presentation::"proposal"
) when {
  !(principal.job == Job::"internal")
};

@createPolicyWhen("Create a template linked policy\n                   when a internal user is added to a prez as viewer")
@id("BobViewInternal")
permit(
  principal == User::"Bob",
  action in [Action::"InternalPrezViewActions"],
  resource == Presentation::"proposal"
) when {
  principal.job == Job::"internal"
};

@id("limit-prez-edit-to-internal")
forbid(
  principal,
  action == Action::"grantEditAccessToPresentation",
  resource
) when {
  !(context.target.job == Job::"internal")
};

@id("limit-prez-view-customer")
forbid(
  principal,
  action == Action::"grantViewAccessToPresentation",
  resource
) when {
  !((!(context.target.job == Job::"customer")) || ((principal.job == Job::"distributor") && (principal.customerId == context.target.customerId)))
};

@id("limit-template-grant-edit-internal")
forbid(
  principal,
  action == Action::"grantEditAccessToTemplate",
  resource
) when {
  (context has targetUser) && (!(context.targetUser.job == Job::"internal"))
};

@id("limit-template-grant-view")
forbid(
  principal,
  action == Action::"grantViewAccessToTemplate",
  resource
) when {
  (context has targetUser) && (context.targetUser.job == Job::"customer") && ((!(principal.job == Job::"distributor")) || (!(principal.customerId == context.targetUser.customerId)))
};

permit(
  principal,
  action in [Action::"TemplateEditActions"],
  resource
) when {
  principal == resource.owner
};

@id("template-edit for owner")
permit(
  principal,
  action in [Action::"PrezEditActions"],
  resource
) when {
  resource.owner == principal
};
