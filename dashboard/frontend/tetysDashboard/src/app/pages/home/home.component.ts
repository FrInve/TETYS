import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'
import { ApiService } from '../../services/api.service'

@Component({
  selector: 'home-page',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent
  ],
  templateUrl: './home.component.html',
})

export class HomePage implements OnInit {

  constructor( 
    public router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.apiService.getData("project").subscribe((res) => {
      console.log(res)
    })
  }

}
