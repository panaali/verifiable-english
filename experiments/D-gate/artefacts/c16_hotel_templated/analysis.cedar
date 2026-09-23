@id("AliceMemberGreen")
permit(
  principal == User::"Alice",
  action in [Action::"viewReservation",Action::"updateReservation",Action::"createReservation"],
  resource in Property::"Green"
);

@id("AliceViewG")
permit(
  principal == User::"Alice",
  action in [Action::"viewReservation"],
  resource in Hotel::"G"
);

@id("BobAdminGreenProp")
permit(
  principal == User::"Bob",
  action in [Action::"viewHotel",Action::"updateHotel",Action::"createHotel",Action::"grantAccessHotel",Action::"viewProperty",Action::"updateProperty",Action::"createProperty",Action::"grantAccessProperty"],
  resource in Property::"Green"
);

@id("BobAdminGreenRes")
permit(
  principal == User::"Bob",
  action in [Action::"viewReservation",Action::"updateReservation",Action::"createReservation",Action::"grantAccessReservation"],
  resource in Property::"Green"
);

@id("BobAdminRProp")
permit(
  principal == User::"Bob",
  action in [Action::"viewHotel",Action::"updateHotel",Action::"createHotel",Action::"grantAccessHotel",Action::"viewProperty",Action::"updateProperty",Action::"createProperty",Action::"grantAccessProperty"],
  resource in Hotel::"R"
);

@id("BobAdminRRes")
permit(
  principal == User::"Bob",
  action in [Action::"viewReservation",Action::"updateReservation",Action::"createReservation",Action::"grantAccessReservation"],
  resource in Hotel::"R"
);
