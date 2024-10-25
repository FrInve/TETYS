import { Component, Input  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './navbar.component.html',
})
export class NavbarComponent {
  @Input() rightSideIconUrl?: string 
  @Input() routingUrl?: string 

  activeTab: string = 'home';

  constructor(  public router: Router  ) {}

  setActiveTab(tab: string) {
    this.activeTab = tab;
  }

  isActive(tab: string): boolean {
    return this.activeTab === tab;
  }

  navigateToRoute() {
    this.router.navigate([`${this.routingUrl}`])
  }
}
