import { Routes } from '@angular/router';

//pages
import { HomePage } from './pages/home/home.component'
import { HealthLandingPage } from './pages/healthLanding/healthLanding.component'
import { EconomyLandingPage } from './pages/economyLanding/economyLanding.component'
import { InclusionLandingPage } from './pages/inclusionLanding/inclusionLanding.component'
import { PeaceLandingPage } from './pages/peaceLanding/peaceLanding.component'
import { SustainabilityLandingPage } from './pages/sustainabilityLanding/sustainabilityLanding.component'
import { AboutDialogComponent } from './pages/about/about.component';
import { DashboardsComponent } from './pages/dashboards/dashboards.component';

import { TopicsComparisonComponent } from './pages/topics-comparison/topics-comparison.component'
import { TopicDetailsComponent } from './pages/topic-details/topic-details.component'

export const routes: Routes = [
    { path: '', component: HomePage },
    { path: 'about', component: AboutDialogComponent },
    { path: 'dashboards', component: DashboardsComponent },

    { path: 'health', component: HealthLandingPage },
    { path: 'economy', component: EconomyLandingPage },
    { path: 'inclusion', component: InclusionLandingPage },
    { path: 'peace', component: PeaceLandingPage },
    { path: 'sustainability', component: SustainabilityLandingPage },
    
    { path: 'health/comparison', component: TopicsComparisonComponent },
    { path: 'economy/comparison', component: TopicsComparisonComponent },
    { path: 'inclusion/comparison', component: TopicsComparisonComponent },
    { path: 'peace/comparison', component: TopicsComparisonComponent },
    { path: 'sustainability/comparison', component: TopicsComparisonComponent },

    { path: 'topic/:topicId', component: TopicDetailsComponent },
];
