import React, { Component } from 'react';
import {
  Route,
  HashRouter,
  Redirect,
  Switch,
} from 'react-router-dom';
import OverviewView from './views/overview.views.js';

class RouteDef extends Component {
  constructor(props) {
    super(props);
    this.props = props;
    this.state = {
    };
  }

  render() {
    return (
      <HashRouter>
        <div id="app-container">
          <header id="header">
            <div id="title">FLOORPLAN EVALUATION</div>
          </header>
          <Switch>
            <Route path="/evaluation" render={() => <OverviewView />} />
            <Redirect to="/evaluation" />
          </Switch>
        </div>
      </HashRouter>
    );
  }
}

export default RouteDef;
