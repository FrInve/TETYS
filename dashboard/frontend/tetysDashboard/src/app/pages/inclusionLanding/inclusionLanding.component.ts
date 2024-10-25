import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'
import { TopicLandingLayoutComponent } from '../../components/topic-landing-layout/topic-landing-layout.component'
import { ApiService } from '../../services/api.service';
import { TopicDataModel } from '../../utils/models'

@Component({
  selector: 'inclusion-landing',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent,
    TopicLandingLayoutComponent
  ],
  templateUrl: './inclusionLanding.component.html',
})

export class InclusionLandingPage {
  topicList: TopicDataModel[] = []

  constructor(
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.apiService.getData(`/project/equality/trending`).subscribe((res) => {
      res.forEach((topic: number) => {
        this.apiService.getData(
          `/topic/${topic}`, 
          {
            project_id: 'equality'
          }
        ).subscribe((topicData) => {
          this.topicList.push(topicData) 
        })
      })
    })
  }
}
