import { Component } from '@angular/core';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'

@Component({
  selector: 'about-dialog',
  standalone: true,
  imports: [
    NavbarComponent
  ],
  templateUrl: './about.component.html',
})
export class AboutDialogComponent {

}
