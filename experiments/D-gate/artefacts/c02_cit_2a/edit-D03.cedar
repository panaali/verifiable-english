// Scenario 2A: Anyone in a given group can view a given photo
permit (
  principal,
  action == Action::"view",
  resource == Photo::"VacationPhoto94.jpg"
)
when { principal in UserGroup::"jane_friends" || principal is Administrator };
