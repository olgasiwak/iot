import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AgmCoreModule } from '@agm/core';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { ListComponent } from './components/list/list.component';
import { HeaderComponent } from './components/header/header.component';
import { AppRoutingModule } from './app-routing.module';
import { NgxSliderModule } from "@angular-slider/ngx-slider";
import { MapComponent } from './components/map/map.component';
import { ApiComponent } from './services/api/api.component';

@NgModule({
  imports: [
    BrowserModule,
    AgmCoreModule.forRoot({
      apiKey: 'AIzaSyApRep9jI-GR1PlGo434LkJlEzit7XvyB8'
    }),
    AppRoutingModule,
    NgxSliderModule,
    HttpClientModule
  ],
  providers: [ApiComponent],
  declarations: [ AppComponent, ListComponent, HeaderComponent, MapComponent, ApiComponent ],
  bootstrap: [ AppComponent ]
})
export class AppModule {}