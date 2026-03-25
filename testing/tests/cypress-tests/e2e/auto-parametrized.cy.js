describe('[AUTO] Cypress', () => {
  const paths = ['account/list','account/create','account/edit','account/delete','device/list','device/create','device/edit','device/delete','charging/list','charging/create','charging/edit','charging/delete','station/list','station/create','station/edit','station/delete','energy/list','energy/create','energy/edit','energy/delete','settlement/list','settlement/create','settlement/edit','settlement/delete','analytics/list','analytics/create','analytics/edit','analytics/delete'];
  
  paths.forEach((path, i) => {
    it('Test ' + i, () => {
      cy.visitAuth('/' + path);
      cy.get('body').should('exist');
    });
  });
});