axe_radius = 1;
ball_radius = 1.25;
cardan_radius = 3;

union()
{
  cylinder(h=2*cardan_radius, r=axe_radius, center=true, $fn=20);
  rotate([0,90,0]) cylinder(h=2*cardan_radius, r=axe_radius, center=true, $fn=20);
}
