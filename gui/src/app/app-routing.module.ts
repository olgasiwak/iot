import { AgmCoreModule } from '@agm/core';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ListComponent } from './components/list/list.component';
import { MapComponent } from './components/map/map.component';

const routes: Routes = [
  { path: '',   redirectTo: 'map', pathMatch: 'full' },
  { path: 'map', component: MapComponent },

  { path: 'list', component: ListComponent }

];

@NgModule({
  imports: [RouterModule.forRoot(routes),
    AgmCoreModule.forRoot({
      apiKey: 'AIzaSyApRep9jI-GR1PlGo434LkJlEzit7XvyB8'
    })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
