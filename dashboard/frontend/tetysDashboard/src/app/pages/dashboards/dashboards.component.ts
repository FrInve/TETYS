import { Component } from '@angular/core';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboards',
  standalone: true,
  imports: [
    NavbarComponent
  ],
  templateUrl: './dashboards.component.html',
})
export class DashboardsComponent {
  constructor(
    public router: Router,
  ) {}
}
