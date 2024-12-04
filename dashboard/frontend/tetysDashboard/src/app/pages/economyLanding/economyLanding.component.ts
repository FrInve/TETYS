import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'
import { TopicLandingLayoutComponent } from '../../components/topic-landing-layout/topic-landing-layout.component'
import { ApiService } from '../../services/api.service';
import { TopicDataModel } from '../../utils/models'
import { LoadingComponent } from '../../components/shared/loading/loading.component'

@Component({
  selector: 'economy-landing',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent,
    TopicLandingLayoutComponent,
    LoadingComponent
  ],
  templateUrl: './economyLanding.component.html',
})

export class EconomyLandingPage implements OnInit {

  topicList: TopicDataModel[] = []
  isLoading = false;

  constructor(
    private apiService: ApiService
  ) {}


  ngOnInit(): void {
    this.isLoading = true
    this.apiService.getData(`/project/economic_development/trending`).subscribe((res) => {
      res.forEach((topic: number) => {
        this.apiService.getData(
          `/topic/${topic}`, 
          {
            project_id: 'economic_development'
          }
        ).subscribe({
          next: (topicData) => {
            this.topicList.push(topicData) 
          },
          complete: () => {
            this.isLoading = false
          }
        })
      })
    })
  }
}
