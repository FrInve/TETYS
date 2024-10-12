import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'
import { TopicLandingLayoutComponent } from '../../components/topic-landing-layout/topic-landing-layout.component'
import { ApiService } from '../../services/api.service';
import { TopicDataModel } from '../../utils/models'

@Component({
  selector: 'sustainability-landing',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent,
    TopicLandingLayoutComponent
  ],
  templateUrl: './sustainabilityLanding.component.html',
})

export class SustainabilityLandingPage {
  topicList: TopicDataModel[] = []

  constructor(
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.apiService.getData(`/project/environmental_sustainability/trending`).subscribe((res) => {
      res.forEach((topic: number) => {
        this.apiService.getData(
          `/topic/${topic}`, 
          {
            project_id: 'environmental_sustainability'
          }
        ).subscribe((topicData) => {
          this.topicList.push(topicData) 
        })
      })
    })
  }
}
